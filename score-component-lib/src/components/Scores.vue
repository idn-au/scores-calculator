<script lang="ts" setup>
import { computed } from "vue";
import { Clock } from "lucide-vue-next";
import type { TopScoreValueObj } from "@idn-au/scores-calculator-js";
import CircleProgress from "@/components/CircleProgress.vue";
import ScoreAccordion from "@/components/ScoreAccordion.vue";
import Modal from "@/components/Modal.vue";
import MobileProgress from "./MobileProgress.vue";

const props = defineProps<{
    title: string;
    score: TopScoreValueObj;
}>();

const createdFormatted = computed(() => {
    const date = new Date(props.score.created + "Z"); // datetime generated in UTC
    return date.toLocaleString();
});
</script>

<template>
    <Modal>
        <template #trigger>
            <div>
                <!-- mobile -->
                <div class="grid gap-2 w-min cursor-pointer hover:bg-accent/50 p-2 md:hidden" :style="{ gridTemplateColumns: `repeat(${title.length}, 1fr)` }">
                    <div v-for="key in props.title.toLowerCase()" class="flex flex-col gap-1 items-center cursor-pointer">
                        <MobileProgress v-if="Object.keys(props.score).length > 0" :value="props.score.scores[key].value" :max="props.score.scores[key].max" tickWhenComplete />
                        <MobileProgress v-else loading />
                        <div class="circle-name text-sm">{{ key.toUpperCase() }}</div>
                    </div>
                </div>
                <!-- desktop -->
                <div class="hidden md:flex flex-col gap-3 cursor-pointer hover:bg-accent/50 p-2">
                    <div class="flex flex-row gap-2 items-center justify-between">
                        <h5>{{ props.title }} Score</h5>
                    </div>
                    <div class="grid gap-2 max-w-[360px]" :style="{ gridTemplateColumns: `repeat(${title.length}, 1fr)` }">
                        <div v-for="key in props.title.toLowerCase()" class="flex flex-col gap-1 items-center cursor-pointer">
                            <CircleProgress v-if="Object.keys(props.score).length > 0" :value="props.score.scores[key].value" :max="props.score.scores[key].max" tickWhenComplete />
                            <CircleProgress v-else loading />
                            <div class="circle-name">{{ key.toUpperCase() }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </template>
        <template #title>{{ props.title }} Score</template>
        <template #description v-if="Object.keys(props.score).length > 0">
            <div class="flex items-center gap-2">
                <span>v{{ props.score.version }},</span>
                <span class="flex items-center gap-1" title="Time created"><Clock class="size-4" /> {{ createdFormatted }}</span>
            </div>
        </template>
        <ScoreAccordion v-if="Object.keys(props.score).length > 0" :scores="props.score.scores" />
    </Modal>
</template>
