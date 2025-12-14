<template>
  <mdui-card :class="selected ? 'card-default' : 'card-selected'">
    <div style="min-height: 72px;">
      <div
        style="height: 48px; width: 300px; padding-left: 16px; padding-top: 18px; display: flex; align-items: center;">
        <div style="
            width: 40px;
            height: 40px;
            background-color: rgb(var(--mdui-color-primary-container));
            border-radius: 50%;
            margin: 4px 8px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Noto Sans SC';
            font-weight: 500;
            font-size: 16px;
            line-height: 24px;
            letter-spacing: 0.1px;
            color: rgb(var(--mdui-on-primary-container));
          ">
          {{ title ? title.charAt(0).toUpperCase() : '' }}
        </div>

        <div style="flex: 1; display: flex; flex-direction: column; padding-left: 8px;">
          <p style="
              font-family: 'Noto Sans SC';
              font-weight: var(--mdui-typescale-title-medium-weight);
              font-size: var(--mdui-typescale-title-medium-size);
              line-height: var(--mdui-typescale-title-medium-line-height);
              letter-spacing: var(--mdui-typescale-title-medium-tracking);
              color: var(--mdui-color-on-surface);
              margin: 0;
              padding-top: 2px;
            ">
            {{ title }}
          </p>
          <p style="
              font-family: 'Noto Sans SC';
              font-weight: var(--mdui-typescale-body-medium-weight);
              font-size: var(--mdui-typescale-body-medium-size);
              line-height: var(--mdui-typescale-body-medium-line-height);
              letter-spacing: var(--mdui-typescale-body-medium-tracking);
              color: var(--mdui-color-on-surface);
              margin: 0;
              padding-bottom: 2px;
            ">
            截止日期 {{ deadline }}
          </p>
        </div>
      </div>
    </div>

    <div style="flex: 1; display: flex; flex-direction: column;">
      <div style="height: 40px; padding: 8px 16px 0 24px;">
        <p style="
            font-family: 'Noto Sans SC';
            font-weight: var(--mdui-typescale-body-medium-weight);
            font-size: var(--mdui-typescale-body-medium-size);
            line-height: var(--mdui-typescale-body-medium-line-height);
            letter-spacing: var(--mdui-typescale-body-medium-tracking);
          
            font-size: 14px;
            color: rgb(var(--mdui-color-on-surface-variant));
            margin: 0;
          ">
          {{ description }}
        </p>
      </div>

    </div>
  </mdui-card>
</template>

<script setup>
const props = defineProps({
  selected: Boolean,
  title: String,
  deadline: String,
  description: String,
});

</script>

<style scoped>
.card-default {
  border-radius: var(--mdui-shape-corner-medium);
  height: 128px;
  display: flex;
  flex-direction: column;
  padding: 0;
  box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
  background-color: rgb(var(--mdui-color-on-primary));
  cursor: default;
  /* 关闭点击手型 */
  transition: box-shadow 0.2s ease;
}

.card-default:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: default;
}

.card-selected {
  border-radius: var(--mdui-shape-corner-medium);
  height: 128px;
  display: flex;
  flex-direction: column;
  padding: 0;
  box-shadow: none;
  background-color: rgb(var(--mdui-color-surface));
  cursor: default;
  transition: box-shadow 0.2s ease;
}

.card-selected:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: default;
}
</style>
