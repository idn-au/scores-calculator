<script lang="ts" setup>
import type { ScoreValueObj } from "@idn-au/scores-calculator-js";
import CircleProgress from "@/components/CircleProgress.vue";
import ScoreAccordion from "@/components/ScoreAccordion.vue";
import Modal from "@/components/Modal.vue";

const props = defineProps<{
    title: string;
    scores: ScoreValueObj;
}>();
</script>

<template>
    <Modal>
        <template #trigger>
            <div class="flex flex-col gap-3">
                <div class="flex flex-row gap-2 items-center justify-between">
                    <h5>{{ props.title }} Score</h5>
                </div>
                <div class="grid gap-2 max-w-[360px]" :style="{ gridTemplateColumns: `repeat(${Object.keys(props.scores).length}, 1fr)` }">
                    <div v-for="[key, score] in Object.entries(props.scores)" class="flex flex-col gap-1 items-center cursor-pointer">
                        <CircleProgress :value="score.value" :max="score.max" tickWhenComplete />
                        <div class="circle-name">{{ key.toUpperCase() }}</div>
                    </div>
                </div>
            </div>
        </template>
        <template #title>{{ props.title }} Score</template>
        <ScoreAccordion :scoreObj="props.scores" />
    </Modal>
</template>
