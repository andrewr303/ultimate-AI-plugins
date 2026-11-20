<template>
  <article>
    <h1>{{ product.name }}</h1>
    <script type="application/ld+json">{{ jsonLd }}</script>
  </article>
</template>

<script setup lang="ts">
const props = defineProps<{ product: { name: string } }>();
useHead({
  script: [{ type: "application/ld+json", innerHTML: JSON.stringify({ "@context": "https://schema.org", "@type": "Product", name: props.product.name }) }],
});
</script>
