<template>
  <button class="base-button" v-bind="$attrs">
    <slot />
  </button>
</template>

<style scoped>
.base-button {
  padding: 8px 16px;
  border-radius: 6px;
  background: var(--color-primary);
  color: white;
  font-weight: 500;
  font-size: var(--font-size-base);
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.base-button:hover { background: var(--color-primary-dark); }
.base-button:active { transform: translateY(1px); }
</style>