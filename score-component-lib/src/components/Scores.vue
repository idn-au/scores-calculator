<script lang="ts" setup>
import type { TopScoreValueObj } from "@idn-au/scores-calculator-js";
import { Comark } from "@comark/vue";
import { Clock, Info, Tag } from "@lucide/vue";
import { computed, ref } from "vue";
import CircleProgress from "@/components/CircleProgress.vue";
import MobileProgress from "@/components/MobileProgress.vue";
import Modal from "@/components/Modal.vue";
import ScoreAccordion from "@/components/ScoreAccordion.vue";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const props = defineProps<TopScoreValueObj & { keys: string; compact?: boolean }>();

const open = ref(false);
const activeKey = ref<string | undefined>(undefined);

const createdFormatted = computed(() => {
    const date = new Date(`${props.created}Z`); // datetime generated in UTC
    return date.toLocaleString("en-AU", { dateStyle: "short", timeStyle: "short" });
});
</script>

<template>
    <div>
        <!-- mobile -->
        <div class="grid gap-2 w-min cursor-pointer p-2 rounded-md md:hidden" :style="{ gridTemplateColumns: `repeat(${props.keys.length}, 1fr)` }" @click="open = true">
            <div v-for="key in props.keys.toLowerCase()" class="flex flex-col gap-1 items-center cursor-pointer">
                <MobileProgress v-if="props.scores && Object.keys(props.scores).length > 0" :value="props.scores[key].value" :max="props.scores[key].max" tickWhenComplete />
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
                    {{ props.title }}
                </h5>
                <Button variant="outline" size="icon-sm" title="Open score" @click="open = true">
                    <Info />
                </Button>
            </div>
            <div class="grid gap-2 max-w-[360px]" :style="{ gridTemplateColumns: `repeat(${props.keys.length}, 1fr)` }">
                <div v-for="key in props.keys.toLowerCase()" class="flex flex-col gap-1 items-center">
                    <CircleProgress
                        v-if="props.scores && Object.keys(props.scores).length > 0"
                        :value="props.scores[key].value"
                        :max="props.scores[key].max"
                        :label="props.compact ? key.toUpperCase() : undefined"
                        :class="`cursor-pointer rounded-full hover:scale-115 transition-all ${props.compact ? '[&_.progress-label]:font-bold [&_.progress-label]:text-base' : ''}`"
                        :tickWhenComplete="!props.compact"
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
            {{ props.title }}
        </template>
        <template #description>
            <div class="flex items-center gap-2">
                <Badge variant="secondary" title="Score version" class="font-mono">
                    <Tag /> {{ props.version }}
                </Badge>
                <Badge variant="outline" title="Time created">
                    <Clock /> {{ createdFormatted }}
                </Badge>
            </div>
        </template>
        <div class="prose dark:prose-invert mb-4 [&_p]:m-0 max-w-[unset]">
            <Suspense>
                <Comark>{{ props.description }}</Comark>
            </Suspense>
        </div>
        <ScoreAccordion v-if="Object.keys(props.scores).length > 0" :scores="props.scores" :defaultValue="activeKey" />
    </Modal>
</template>
