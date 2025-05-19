<script lang="ts" setup>
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";

const model = defineModel<boolean>();
</script>

<template>
    <Dialog v-model:open="model">
        <DialogTrigger as-child>
            <slot name="trigger" />
        </DialogTrigger>
        <DialogContent class="w-[90%] sm:max-w-[800px] grid-rows-[auto_minmax(0,1fr)_auto] p-0 max-h-[90dvh]">
            <DialogHeader class="p-6 pb-0">
                <DialogTitle v-if="$slots.title">
                    <slot name="title" />
                </DialogTitle>
                <DialogDescription v-if="$slots.description">
                    <slot name="description" />
                </DialogDescription>
            </DialogHeader>
            <div class="modal-content pt-4 px-6 overflow-y-auto">
                <slot />
            </div>
            <DialogFooter v-if="$slots.footer" class="p-6 pt-0 sm:justify-between">
                <slot name="footer" />
            </DialogFooter>
        </DialogContent>
    </Dialog>
</template>
