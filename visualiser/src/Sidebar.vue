<template>
  <div class="sidebar">
    <h2>Visualiser</h2>

    <Modeswitch
      :options="options"
      default-key="e2e"
    />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import Modeswitch, { Option } from './components/ModeSwitch.vue'

@Component({
  components: {
    Modeswitch
  }
})
export default class Sidebar extends Vue {

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

}
</script>

<style lang="scss">

.sidebar {
  padding: var(--padding-v-large) var(--padding-h-large);

  h2 {
    font-weight: bold;
  }
}
</style>