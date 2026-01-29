<script lang="ts" setup>
import { computed } from "vue";
import { Check } from "lucide-vue-next";
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
    if (props.value != undefined && props.max != undefined) {
        return props.value / props.max * 100;
    } else if (props.percentage != undefined) {
        return props.percentage;
    } else {
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
    <div v-if="props.loading" class="relative w-full">
        <Skeleton class="rounded-full aspect-square" />
        <div class="rounded-full bg-background text-foreground flex items-center justify-center absolute inset-2">
            <Skeleton class="rounded w-5 h-4" />
        </div>
    </div>
    <div v-else class="rounded-full w-full aspect-square relative shrink-0" :style="{ background: `conic-gradient(${percentGradient} ${percent}%, 0, rgba(80, 80, 80, 0.2) ${100 - percent}%)` }">
        <div class="rounded-full bg-background text-foreground flex items-center justify-center absolute inset-2">
            <span class="text-sm">
                <template v-if="props.label">{{ props.label }}</template>
                <template v-else-if="props.tickWhenComplete && percent === 100">
                    <Check class="size-6" />
                </template>
                <template v-else-if="props.value != undefined && props.max != undefined">{{ props.value }}/{{ props.max }}</template>
                <template v-else>{{ percent }}%</template>
            </span>
        </div>
    </div>
</template>
