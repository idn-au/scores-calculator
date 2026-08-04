<script lang="ts" setup>
import type { TopScoreValueObj } from "@idn-au/scores-calculator-js";
import { Clock, Info } from "lucide-vue-next";
import { computed, ref } from "vue";
import CircleProgress from "@/components/CircleProgress.vue";
import Modal from "@/components/Modal.vue";
import ScoreAccordion from "@/components/ScoreAccordion.vue";
import { Button } from "@/components/ui/button";
import MobileProgress from "./MobileProgress.vue";

const props = defineProps<{
    title: string;
    score: TopScoreValueObj;
    compact?: boolean;
}>();

const open = ref(false);
const activeKey = ref<string | undefined>(undefined);

const createdFormatted = computed(() => {
    const date = new Date(`${props.score.created}Z`); // datetime generated in UTC
    return date.toLocaleString();
});
</script>

<template>
    <div>
        <!-- mobile -->
        <div class="grid gap-2 w-min cursor-pointer p-2 rounded-md md:hidden" :style="{ gridTemplateColumns: `repeat(${title.length}, 1fr)` }" @click="open = true">
            <div v-for="key in props.title.toLowerCase()" class="flex flex-col gap-1 items-center cursor-pointer">
                <MobileProgress v-if="Object.keys(props.score).length > 0" :value="props.score.scores[key].value" :max="props.score.scores[key].max" tick-when-complete />
                <MobileProgress v-else loading />
                <div class="circle-name text-sm font-bold">
                    {{ key.toUpperCase() }}
                </div>
            </div>
        </div>
        <!-- desktop -->
        <div class="hidden md:flex flex-col gap-3 p-2 rounded-md w-fit">
            <div v-if="!props.compact" class="flex flex-row gap-2 items-center justify-between">
                <h5 class="font-bold">
                    {{ props.title }} Score
                </h5>
                <Button variant="outline" size="icon-sm" title="Open score" @click="open = true">
                    <Info />
                </Button>
            </div>
            <div class="grid gap-2 max-w-[360px]" :style="{ gridTemplateColumns: `repeat(${title.length}, 1fr)` }">
                <div v-for="key in props.title.toLowerCase()" class="flex flex-col gap-1 items-center">
                    <CircleProgress
                        v-if="Object.keys(props.score).length > 0"
                        :value="props.score.scores[key].value"
                        :max="props.score.scores[key].max"
                        :label="props.compact ? key.toUpperCase() : undefined"
                        :class="`cursor-pointer rounded-full hover:scale-115 transition-all ${props.compact ? '[&_.progress-label]:font-bold [&_.progress-label]:text-base' : ''}`"
                        :tick-when-complete="!props.compact"
                        @click="activeKey = key; open = true"
                    />
                    <CircleProgress v-else loading />
                    <div v-if="!props.compact" class="circle-name font-bold">
                        {{ key.toUpperCase() }}
                    </div>
                </div>
            </div>
        </div>
    </div>
    <Modal v-model="open" @close="activeKey = undefined">
        <template #title>
            {{ props.title }} Score
        </template>
        <template v-if="Object.keys(props.score).length > 0" #description>
            <div class="flex items-center gap-2">
                <span>v{{ props.score.version }},</span>
                <span class="flex items-center gap-1" title="Time created">
                    <Clock class="size-4" /> {{ createdFormatted }}
                </span>
            </div>
        </template>
        <!--	    score description? -->
        <ScoreAccordion v-if="Object.keys(props.score).length > 0" :scores="props.score.scores" :default-value="activeKey" />
    </Modal>
</template>
