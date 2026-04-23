<template>
  <button type="button" class="base-button" v-bind="$attrs">
    <slot />
  </button>
</template>

<style scoped>
.base-button {
  padding: 8px 16px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  font-size: var(--font-size-base);
  background: linear-gradient(145deg, var(--color-primary), var(--color-primary-dark));
  border: none;
  cursor: pointer;

  /* 3D effect */
  transform: perspective(200px) rotateX(2deg) translateY(2px);
  margin-bottom: 6px;
  transition: 0.2s;
}

.base-button:hover {
  transform: perspective(200px) rotateX(10deg);
}

.base-button:active {
  transform: perspective(200px) rotateX(8deg) scale(0.98);
  transform-origin: center bottom;
  transition: transform 0.1s ease, background 0.2s ease;
}
</style>