<template>
  <MglMarker :coordinates="coordinate">
    <div
      slot="marker"
      class="marker-container"
    >
      <img
        ref="marker"
        class="marker"
        src="@/icons/drone.png"
        :style="rotationStyle"
      >
    </div>
  </MglMarker>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'
import { MglMarker } from "vue-mapbox"

@Component({
  components: {
    MglMarker
  }
})
export default class DroneMarker extends Vue {

  @Prop()
  public readonly coordinate: number[]

  @Prop()
  public readonly bearing: number

  get rotationStyle(): string {
    return `transform: rotate(${this.bearing}deg)`
  }
}
</script>

<style lang="scss">

.marker-container {
  width: 100px;
  height: 100px;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}

.marker {
  display: inline-block;
  transform-origin: center;
  width: 100px;
  height: 100px;
}

</style>
