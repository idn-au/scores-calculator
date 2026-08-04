<script lang="ts" setup>
import { Square, SquareCheckBig } from "lucide-vue-next";
import type { ScoreValueObj } from "@idn-au/scores-calculator-js";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import CircleProgress from "@/components/CircleProgress.vue";

const props = defineProps<{
    scores: ScoreValueObj;
	defaultValue?: string;
}>();
</script>

<template>
    <Accordion type="single" collapsible :defaultValue="defaultValue">
        <AccordionItem v-for="[key, score] in Object.entries(props.scores)" :value="key" class="">
            <AccordionTrigger class="cursor-pointer hover:bg-accent/50 hover:no-underline p-4">
                <div class="flex flex-row gap-4 grow items-start">
                    <CircleProgress :value="score.value" :max="score.max" class="max-w-16 md:max-w-20 transition-all" />
                    <div class="flex flex-col gap-2 text-left grow">
                        <h3>{{ score.title }}</h3>
                        <p class="text-sm text-muted-foreground">{{ score.description }}</p>
                    </div>
                </div>
            </AccordionTrigger>
            <AccordionContent class="p-0">
                <Card v-if="score.scores" class="p-0 m-4">
                    <CardContent class="p-0">
                        <ScoreAccordion :scores="score.scores" class="" />
                    </CardContent>
                </Card>
                <div v-else-if="score.requirements" class="flex flex-col gap-2 p-4">
                    <div v-if="score.prerequisites" :class="`flex flex-row gap-2 items-start mb-2 ${score.prerequisites.enabled ? '' : 'text-muted-foreground'}`">
                        <SquareCheckBig v-if="score.prerequisites.enabled" class="size-4 shrink-0 mt-0.5" />
                        <Square v-else class="size-4 shrink-0 mt-0.5" />
                        <span>If {{ score.prerequisites.conditions.map(c => c.title).join(' and ') }} then the following scores can be assigned:</span>
                    </div>
                    <div v-for="requirement in score.requirements" :class="`flex flex-row gap-2 items-start ${requirement.enabled && (score.prerequisites ? score.prerequisites.enabled : true) ? '' : 'text-muted-foreground'} ${score.prerequisites ? 'ml-3' : ''}`">
                        <SquareCheckBig v-if="requirement.enabled" class="size-4 shrink-0 mt-0.5" />
                        <Square v-else class="size-4 shrink-0 mt-0.5" />
                        <span>{{ requirement.description }}</span>
                        <span>[{{ requirement.value }}]</span>
                    </div>
                </div>
            </AccordionContent>
        </AccordionItem>
    </Accordion>
</template>
