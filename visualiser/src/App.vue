<template>
  <div id="app">
    <Sidebar
      :core="core"
      :vehicle="vehicle"
      :connected="connected"
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
    </MglMap>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
import Mapbox from "mapbox-gl"
import { MglMap } from "vue-mapbox"

import DroneMarker from './DroneMarker.vue'
import Sidebar from './Sidebar.vue'

import manager, { UpdateMessage } from './lib/manager'

@Component({
  components: {
    MglMap,
    DroneMarker,
    Sidebar
  }
})
export default class App extends Vue {

  // Longitude, latitude
  private position: [number, number] = [149.165230, -35.363261]
  private heading = 0

  private map = null

  private tracks = {
    drone: null,
    person: null
  }

  private core = {}
  private vehicle = {}
  private connected = false

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

      if (data.person)
        this.updateTrack([data.person.global.longitude, data.person.global.latitude], 'person')
    }

    manager.onreset = () => {
      this.position = [149.165230, -35.363261]
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

</style>
