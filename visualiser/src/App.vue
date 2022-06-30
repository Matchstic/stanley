<template>
  <div id="app">
    <Sidebar
      :core="core"
      :vehicle="vehicle"
      :connected="connected"
      :person="person"
    />

    <MglMap
      class="map"
      :access-token="mapboxToken"
      :map-style="mapboxStyle"
      :min-zoom="14"
      :center="position"
      :zoom="zoom"
      :drag-rotate="false"
      :touch-zoom-rotate="false"
      @load="onMapLoaded"
    >
      <DroneMarker
        :coordinate="position"
        :bearing="heading"
      />

      <MglMarker :coordinates="personPosition">
        <img
          slot="marker"
          class="person-marker"
          src="@/icons/person.png"
        >
      </MglMarker>
    </MglMap>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Mapbox from "mapbox-gl"
import { MglMap, MglMarker } from "vue-mapbox"

import DroneMarker from './DroneMarker.vue'
import Sidebar from './Sidebar.vue'

import manager, { UpdateMessage } from './lib/manager'

import { ResponsiveGamepad } from 'responsive-gamepad'

@Component({
  components: {
    MglMap,
    MglMarker,
    DroneMarker,
    Sidebar
  }
})
export default class App extends Vue {

  // Longitude, latitude
  private position: [number, number] = [149.165230, -35.363261]
  private heading = 0
  private personPosition: [number, number] = [149.165230, -35.363203]

  private map = null

  private tracks = {
    drone: null,
    person: null
  }

  private core = {}
  private vehicle = {}
  private person = {}
  private connected = false
  private inputLoop = null

  created() {
    manager.onconnected = (data: boolean) => {
      this.connected = data
    }

    manager.onchange = (data: UpdateMessage) => {
      this.position = [data.vehicle.coordinates.longitude, data.vehicle.coordinates.latitude]
      this.heading = data.vehicle.heading

      this.core = data.core
      this.vehicle = data.vehicle

      // TODO: handle person information

      // Update map trace
      this.updateTrack(this.position, 'drone')

      if (data.person) {
        this.person = data.person
        this.updateTrack([data.person.global.longitude, data.person.global.latitude], 'person')
      } else {
        this.person = {}
      }
    }

    manager.onreset = () => {
      this.position = [149.165230, -35.363261]
      this.personPosition = [149.165230, -35.363203]
      this.heading = 0

      // Clear map state
      const clean = (name: string) => {
        this.map.removeLayer(name)
        this.map.removeSource(name)
      }

      clean('drone')
      clean('person')

      this.prepareMap()
    }

    ResponsiveGamepad.enable()
    this.startInputTracking()
  }

  private startInputTracking() {
    const INTERVAL = 50 // ms
    const SPEED = 1.5 // m/s
    const MOVE_DISTANCE = SPEED * (INTERVAL / 1000)
    const EARTH = 6378137

    this.inputLoop = setInterval(() => {
      const { DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT } = ResponsiveGamepad.getState()
      const [startLongitude, startLatitude] = this.personPosition

      let north = 0
      let east = 0

      if (DPAD_UP && !DPAD_DOWN) {
        // Upwards
        north = MOVE_DISTANCE
      } else if (!DPAD_UP && DPAD_DOWN) {
        // Downwards
        north = -MOVE_DISTANCE
      }

      if (DPAD_LEFT && !DPAD_RIGHT) {
        // left
        east = -MOVE_DISTANCE
      } else if (!DPAD_LEFT && DPAD_RIGHT) {
        // right
        east = MOVE_DISTANCE
      }

      // Coordinate offsets in radians
      const dLat = north / EARTH
      const dLon = east / (EARTH * Math.cos(Math.PI * startLatitude / 180))

      // OffsetPosition, decimal degrees
      const latOffset = startLatitude + dLat * (180 / Math.PI)
      const lonOffset = startLongitude + dLon * (180 / Math.PI)

      this.personPosition = [lonOffset, latOffset]

      manager.send({
        type: 'control',
        latitude: latOffset,
        longitude: lonOffset
      })
    }, INTERVAL)
  }

  private onMapLoaded(event) {
    this.map = event.map
    this.prepareMap()
  }

  private prepareMap() {
    this.tracks = {
      drone: this.generateFeatureCollection(),
      person: this.generateFeatureCollection()
    }

    this.map.addSource('drone', { type: 'geojson', data: this.tracks.drone })
    this.map.addLayer({
      'id': 'drone',
      'type': 'line',
      'source': 'drone',
      'paint': {
        'line-color': 'yellow',
        'line-opacity': 0.75,
        'line-width': 2
      }
    })

    this.map.addSource('person', { type: 'geojson', data: this.tracks.person })
    this.map.addLayer({
      'id': 'person',
      'type': 'line',
      'source': 'person',
      'paint': {
        'line-color': 'blue',
        'line-opacity': 0.75,
        'line-width': 2
      }
    })
  }

  private generateFeatureCollection() {
    return {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: []
          }
        }
      ]
    }
  }

  private updateTrack(coord, trackName) {
    const trackData = this.tracks[trackName]
    trackData.features[0].geometry.coordinates.push(coord)

    this.map.getSource(trackName).setData(trackData)
  }

  get zoom(): number {
    return 18
  }

  get url(): string {
    const id = 'streets-v11'
    return `https://api.mapbox.com/styles/v1/mapbox/${id}/tiles/{z}/{x}/{y}?access_token=${this.mapboxToken}`
  }

  get mapboxToken(): string {
    // eslint-disable-next-line no-undef
    return process.env.VUE_APP_MAPBOX_TOKEN
  }

  get mapboxStyle(): string {
    return 'mapbox://styles/mapbox/satellite-streets-v11'
  }
}
</script>

<style lang="scss">

@import './styles/main.scss';
@import './styles/layout.scss';

#app {
	color: var(--text-color);
	position: relative;

	margin: 0;
	padding: 0;

	height: 100%;
	min-height: 100vh;
	width: 100%;

  display: flex;
  flex-direction: row;
  justify-content: flex-start;

  .map {
    flex: 1 1 auto;
    height: 100vh;
  }

  .sidebar {
    flex: 0 0 350px;
  }
}

.person-marker {
  display: inline-block;
  transform-origin: center;
  width: 30px;
  height: 30px;
}

</style>
