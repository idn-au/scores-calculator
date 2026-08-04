<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { Check } from "lucide-vue-next";
import { ProgressIndicator, ProgressRoot } from "reka-ui";
import { computed } from "vue";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const props = defineProps<{
    value?: number;
    max?: number;
    percentage?: number;
    label?: string;
    tickWhenComplete?: boolean;
    loading?: boolean;
    class?: HTMLAttributes["class"];
}>();

const RADIUS = 42;
const STROKE_WIDTH = 12;
const circumference = 2 * Math.PI * RADIUS;
const trackPath = `
  M 50 50
  m 0 -${RADIUS}
  a ${RADIUS} ${RADIUS} 0 1 1 0 ${RADIUS * 2}
  a ${RADIUS} ${RADIUS} 0 1 1 0 -${RADIUS * 2}
  `;

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

const dashOffset = computed(() => (percent.value / 100) * circumference);
</script>

<template>
    <div :class="cn('relative shrink-0', props.class)">
        <ProgressRoot v-model="percent" as-child>
            <svg :class="`w-full h-full ${props.loading ? 'animate-pulse' : ''}`" viewBox="0 0 100 100">
                <path :d="trackPath" class="fill-none stroke-muted" :style="{ 'stroke-width': `${STROKE_WIDTH}px` }" />
                <ProgressIndicator as-child>
                    <path
                        :d="trackPath"
                        class="fill-none transition-[stroke-dasharray,opacity] duration-700 data-[value='0']:opacity-0"
                        :style="{
                            'stroke-linecap': 'round',
                            'stroke-dasharray': `${dashOffset}px, ${circumference}px`,
                            'stroke-dashoffset': '0px',
                            'stroke': percentGradient,
                            'stroke-width': `${STROKE_WIDTH}px`,
                        }"
                    />
                </ProgressIndicator>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
                <span class="progress-label text-sm">
                    <Skeleton v-if="props.loading" class="rounded w-5 h-4" />
                    <template v-else-if="props.label">{{ props.label }}</template>
                    <Check v-else-if="props.tickWhenComplete && percent === 100" class="size-6" />
                    <template v-else-if="props.value !== undefined && props.max !== undefined">{{ props.value }}/{{ props.max }}</template>
                    <template v-else>{{ percent }}%</template>
                </span>
            </div>
        </ProgressRoot>
    </div>
</template>
