<script lang="ts" setup>
import { Check } from "@lucide/vue";
import { computed } from "vue";
import { Skeleton } from "@/components/ui/skeleton";

const props = defineProps<{
    value?: number;
    max?: number;
    percentage?: number;
    label?: string;
    tickWhenComplete?: boolean;
    loading?: boolean;
}>();

const percent = computed(() => {
    if (props.value !== undefined && props.max !== undefined) {
        return props.value / props.max * 100;
    }
    else if (props.percentage !== undefined) {
        return props.percentage;
    }
    else {
        return 0;
    }
});

const percentGradient = computed(() => {
    const minHue = 0; // red
    const maxHue = 130; // green
    return `hsl(${percent.value / 100 * (maxHue - minHue)}, 100%, 48%)`;
});
</script>

<template>
    <Skeleton v-if="props.loading" class="size-4 rounded" />
    <div v-else class="size-4 flex items-center justify-center rounded" :style="{ background: percentGradient }">
        <Check v-if="props.tickWhenComplete && percent === 100" class="size-4 text-black" />
    </div>
</template>
