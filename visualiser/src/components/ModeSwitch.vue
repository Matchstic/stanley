<template>
  <div class="modeswitch">
    <div
      v-for="option in options"
      :key="option.key"
      class="option"
      :class="{ enabled: option.key === currentKey }"
      @click.prevent.stop="onOptionClick(option.key)"
    >
      <span>{{ option.title }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator'

export type Option = {
  title: string
  key: string
}

@Component
export default class Modeswitch extends Vue {

  @Prop()
  public readonly options: Option[]

  @Prop()
  public readonly defaultKey: string

  private currentKey = ''

  created(): void {
    this.currentKey = this.defaultKey
  }

  onOptionClick(key: string): void {
    this.currentKey = key
    this.$emit('changed', key)
  }
}
</script>

<style lang="scss">

.modeswitch {
  padding: var(--padding-v-tiny);
  background: var(--button-color);

  height: 30px;

  border-radius: var(--border-radius);

  display: flex;
  flex-direction: row;
  align-items: center;

  .option {
    border-radius: var(--border-radius-small);
    cursor: pointer;

    flex: 1 1 33%;
    height: calc(30px - var(--padding-v-tiny) * 2);

    display: flex;
    align-items: center;
    justify-content: center;

    &.enabled {
      background-color: var(--input-color);
      color: var(--text-color-inverse);
    }

    &:hover {
      opacity: 0.75;
    }
  }
}
</style>