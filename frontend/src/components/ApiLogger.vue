<script setup>
const props = defineProps({ logs: { type: Array, required: true } })

function formatData(data) {
  if (data === null || data === undefined) return String(data)
  if (typeof data === 'object') return JSON.stringify(data, null, 2)
  return String(data)
}

function getClass(type) {
  switch(type) {
    case 'request': return 'log-request'
    case 'success': return 'log-success'
    case 'error': return 'log-error'
    default: return ''
  }
}
</script>

<template>
  <div class="api-logger">
    <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="getClass(log.type)">
      <strong>{{ log.title }}</strong>
      <pre>{{ formatData(log.data) }}</pre>
    </div>
  </div>
</template>

<style scoped>
.api-logger {
  position: fixed;
  top: 100px;
  right: 0;
  width: 300px;
  height: 80vh;
  padding: 12px;
  font-family: monospace;
  font-size: 13px;
  background: #f7f7f7;
  border-left: 1px solid #ddd;
  overflow-y: auto;
  box-shadow: -2px 0 8px rgba(0,0,0,0.05);
  z-index: 100;
}
.log-entry {
  margin-bottom: 12px;
  padding: 8px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
.log-request { border: 1px solid #2196f3; background: #e3f2fd; color: #0d47a1; }
.log-success { border: 1px solid #4caf50; background: #e8f5e9; color: #1b5e20; }
.log-error { border: 1px solid #f44336; background: #ffebee; color: #b71c1c; }
pre { margin: 4px 0 0 0; white-space: pre-wrap; word-wrap: break-word; }
</style>
