<script lang="ts" setup>
import { Square, SquareCheckBig } from "lucide-vue-next";
import type { ScoreValueObj } from "@idn-au/scores-calculator-js";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import CircleProgress from "@/components/CircleProgress.vue";

const props = defineProps<{
    scoreObj: ScoreValueObj;
}>();
</script>

<template>
    <Accordion type="single" collapsible>
        <AccordionItem v-for="[key, score] in Object.entries(props.scoreObj)" :value="key">
            <AccordionTrigger>
                <div class="flex flex-row gap-4 flex-grow">
                    <CircleProgress :value="score.value" :max="score.max" class="max-w-20" />
                    <div class="flex flex-col gap-2 text-left flex-grow">
                        <h3>{{ score.title }}</h3>
                        <p class="text-sm text-muted-foreground">{{ score.description }}</p>
                    </div>
                </div>
            </AccordionTrigger>
            <AccordionContent>
                <Card v-if="score.scores">
                    <CardContent>
                        <ScoreAccordion :scoreObj="score.scores" class="ml-4" />
                    </CardContent>
                </Card>
                <div v-else-if="score.requirements" class="flex flex-col gap-2">
                    <div v-if="score.prerequisites" :class="`flex flex-row gap-2 items-start mb-2 ${score.prerequisites.enabled ? '' : 'text-muted-foreground'}`">
                        <SquareCheckBig v-if="score.prerequisites.enabled" class="h-4 w-4 shrink-0" />
                        <Square v-else class="h-4 w-4 shrink-0" />
                        <span>If {{ score.prerequisites.conditions.map(c => c.title).join(' and ') }} then the following scores can be assigned:</span>
                    </div>
                    <div v-for="requirement in score.requirements" :class="`flex flex-row gap-2 items-start ${requirement.enabled && (score.prerequisites ? score.prerequisites.enabled : true) ? '' : 'text-muted-foreground'} ${score.prerequisites ? 'ml-3' : ''}`">
                        <SquareCheckBig v-if="requirement.enabled" class="h-4 w-4 shrink-0" />
                        <Square v-else class="h-4 w-4 shrink-0" />
                        <span>{{ requirement.description }}</span>
                        <span>[{{ requirement.value }}]</span>
                    </div>
                </div>
            </AccordionContent>
        </AccordionItem>
    </Accordion>
</template>
