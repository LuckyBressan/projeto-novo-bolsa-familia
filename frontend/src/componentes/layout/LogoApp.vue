<template>
  <svg class="logo" width="36" height="36" viewBox="0 0 36 36" aria-hidden="true">
    <rect class="logo__barra-a" x="2" y="18" width="8" height="16" rx="2" />
    <rect class="logo__barra-centro" x="14" y="8" width="8" height="26" rx="2" />
    <rect class="logo__barra-b" x="26" y="13" width="8" height="21" rx="2" />
  </svg>
</template>

<style scoped>
.logo {
  flex: none;
}

.logo__barra-a {
  fill: var(--series-1);
}

.logo__barra-centro {
  fill: var(--interactive);
}

.logo__barra-b {
  fill: var(--series-2);
}
</style>
