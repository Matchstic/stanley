<template>
  <div class="sidebar">
    <h2>Visualiser</h2>

    <Modeswitch
      :options="options"
      default-key="e2e"
    />

    <div class="sidebar-data">
      <div class="sidebar-datum large">
        {{ state }}
        <span>State</span>
      </div>

      <div class="sidebar-datum">
        {{ linkState }}
        <span>Link</span>
      </div>

      <div class="sidebar-datum">
        {{ altitude }}m
        <span>Altitude</span>
      </div>

      <div class="sidebar-datum">
        {{ heading }}deg
        <span>Heading</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

import Modeswitch, { Option } from './components/ModeSwitch.vue'

@Component({
  components: {
    Modeswitch
  }
})
export default class Sidebar extends Vue {

  @Prop()
  public readonly core: {
    state: string
  }

  @Prop()
  public readonly vehicle: {
    heading: number
    altitude: number
  }

  @Prop()
  public readonly connected: boolean

  get options(): Option[] {
    return [
      {
        title: 'E2E',
        key: 'e2e'
      },
      {
        title: 'Manual',
        key: 'manual'
      },
      {
        title: 'Playback',
        key: 'playback'
      }
    ]
  }

  get altitude(): number {
    return this.vehicle?.altitude || 0
  }

  get heading(): number {
    return this.vehicle?.heading || 0
  }

  get state(): string {
    return this.core?.state || 'UNKNOWN'
  }

  get linkState(): string {
    return this.connected ? 'TRUE' : 'FALSE'
  }
}
</script>

<style lang="scss">

.sidebar {
  padding: var(--padding-v-large) var(--padding-h-large);

  h2 {
    font-weight: bold;
  }
}

.sidebar-data {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;

  width: 100%;

  .sidebar-datum {
    width: 33%;
    display: flex;

    margin-top: var(--padding-v-large);

    flex-direction: column;
    align-items: center;

    &.large {
      width: 100%;
    }

    span {
      margin-top: var(--padding-v);
      font-weight: bold;
      color: var(--item-text-color);
    }
  }
}
</style>