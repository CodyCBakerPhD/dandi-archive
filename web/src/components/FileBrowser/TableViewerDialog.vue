<template>
  <v-dialog
    v-model="open"
    max-width="90vw"
    scrollable
  >
    <v-card v-if="item">
      <v-card-title class="d-flex align-center">
        <v-icon
          class="mr-2"
          color="primary"
        >
          mdi-table
        </v-icon>
        <span
          class="text-truncate"
          :title="item.path"
        >{{ name }}</span>
        <v-spacer />
        <v-tooltip location="bottom">
          <template #activator="{ props: rawProps }">
            <v-btn
              icon
              variant="text"
              :href="inlineUri"
              target="_blank"
              rel="noreferrer"
              v-bind="rawProps"
            >
              <v-icon color="primary">
                mdi-file-document-outline
              </v-icon>
            </v-btn>
          </template>
          <span>View raw file</span>
        </v-tooltip>
        <v-tooltip location="bottom">
          <template #activator="{ props: downloadProps }">
            <v-btn
              icon
              variant="text"
              :href="downloadUri"
              v-bind="downloadProps"
            >
              <v-icon color="primary">
                mdi-download
              </v-icon>
            </v-btn>
          </template>
          <span>Download asset</span>
        </v-tooltip>
        <v-btn
          icon
          variant="text"
          @click="open = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-progress-linear
        v-if="loading"
        indeterminate
      />

      <v-card-text style="max-height: 70vh;">
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
        >
          {{ error }}
        </v-alert>

        <template v-else-if="!loading">
          <v-alert
            v-if="truncated"
            type="info"
            variant="tonal"
            density="compact"
            class="mb-3"
          >
            This file is large, so only the first {{ rows.length }} rows are shown.
            Download the file to see its full contents.
          </v-alert>

          <div class="d-flex align-center mb-2">
            <v-text-field
              v-model="search"
              label="Search table"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              variant="outlined"
              hide-details
              clearable
              style="max-width: 20em;"
            />
            <v-checkbox
              v-model="firstRowIsHeader"
              label="First row is a header"
              density="compact"
              hide-details
              class="ml-4 flex-grow-0"
            />
            <v-spacer />
            <span class="text-caption text-medium-emphasis">
              {{ dataRows.length }} rows &times; {{ columnCount }} columns
            </span>
          </div>

          <v-data-table
            v-if="dataRows.length"
            :headers="headers"
            :items="tableItems"
            :search="search"
            :items-per-page="25"
            density="compact"
            class="table-viewer"
            fixed-header
          />
          <v-banner v-else>
            This file is empty.
          </v-banner>
        </template>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import type { Ref } from 'vue';
import { computed, ref, watch } from 'vue';
import axios from 'axios';

import type { AssetPath } from '@/types';
import { dandiRest } from '@/rest';
import type { Delimiter } from '@/utils/tabular';
import { parseDelimitedText, tabularDelimiter } from '@/utils/tabular';

// Guardrails, so that a pathologically large file can't lock up the browser.
const MAX_FILE_SIZE = 50e6;
const MAX_ROWS = 5000;

const props = defineProps<{
  modelValue: boolean,
  item: AssetPath | null,
  identifier: string,
  version: string,
}>();

const emit = defineEmits<{(e: 'update:modelValue', value: boolean): void}>();

const open = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
});

const loading = ref(false);
const error: Ref<string | null> = ref(null);
const rows: Ref<string[][]> = ref([]);
const truncated = ref(false);
const search = ref('');
const firstRowIsHeader = ref(true);

const name = computed(() => props.item?.path.split('/').pop() || '');
const assetId = computed(() => props.item?.asset?.asset_id || null);
const inlineUri = computed(() => (
  assetId.value ? dandiRest.assetInlineURI(props.identifier, props.version, assetId.value) : ''
));
const downloadUri = computed(() => (
  assetId.value ? dandiRest.assetDownloadURI(props.identifier, props.version, assetId.value) : ''
));

const columnCount = computed(
  () => rows.value.reduce((max, row) => Math.max(max, row.length), 0),
);
const dataRows = computed(() => (
  firstRowIsHeader.value ? rows.value.slice(1) : rows.value
));
const headers = computed(() => {
  const headerRow = firstRowIsHeader.value ? rows.value[0] || [] : [];
  return Array.from({ length: columnCount.value }, (_, i) => ({
    title: headerRow[i] || `Column ${i + 1}`,
    key: `c${i}`,
  }));
});
const tableItems = computed(() => dataRows.value.map(
  (row) => Object.fromEntries(
    Array.from({ length: columnCount.value }, (_, i) => [`c${i}`, row[i] ?? '']),
  ),
));

async function loadFile() {
  const { item } = props;
  if (!item?.asset) {
    return;
  }

  const delimiter: Delimiter | null = tabularDelimiter(item.path);
  if (delimiter === null) {
    error.value = 'This file is not a supported tabular file.';
    return;
  }

  loading.value = true;
  error.value = null;
  rows.value = [];
  truncated.value = false;
  search.value = '';
  firstRowIsHeader.value = true;

  if (item.aggregate_size > MAX_FILE_SIZE) {
    error.value = 'This file is too large to preview in the browser.'
      + ' Please download it to view its contents.';
    loading.value = false;
    return;
  }

  try {
    const { data } = await axios.get<string>(inlineUri.value, {
      responseType: 'text',
      // Ensure that the response isn't parsed as JSON/XML by axios.
      transformResponse: [(response) => response],
    });
    const parsed = parseDelimitedText(data, delimiter);
    truncated.value = parsed.length > MAX_ROWS;
    rows.value = truncated.value ? parsed.slice(0, MAX_ROWS) : parsed;
  } catch {
    error.value = 'Failed to load this file. You can still download it or view it raw.';
  } finally {
    loading.value = false;
  }
}

watch(() => [props.modelValue, props.item], () => {
  if (props.modelValue && props.item) {
    loadFile();
  }
}, { immediate: true });
</script>

<style scoped>
.table-viewer :deep(td) {
  white-space: nowrap;
}
</style>
