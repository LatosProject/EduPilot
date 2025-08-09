<template>
  <mdui-card :class="selected ? 'card-selected' : 'card-default'">
    <div style="min-height: 72px;">
      <div
        style="height: 48px; width: 300px; padding-left: 16px; padding-top: 18px; display: flex; align-items: center;">
        <div style="
            width: 40px;
            height: 40px;
            background-color: #eaddff;
            border-radius: 50%;
            margin: 4px 8px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            font-size: 16px;
            line-height: 24px;
            letter-spacing: 0.1px;
            color: #4f378a;
          ">
          {{ title ? title.charAt(0).toUpperCase() : '' }}
        </div>

        <div style="flex: 1; display: flex; flex-direction: column; padding-left: 8px;">
          <p style="
              font-family: 'Roboto', sans-serif;
              font-weight: 600;
              font-size: 16px;
              line-height: 24px;
              letter-spacing: 0.15px;
              color: #1d1b20;
              margin: 0;
              padding-top: 2px;
            ">
            {{ title }}
          </p>
          <p style="
              font-family: 'Roboto', sans-serif;
              font-weight: 400;
              font-size: 14px;
              line-height: 20px;
              letter-spacing: 0.25px;
              color: #1d1b20;
              margin: 0;
              padding-bottom: 2px;
            ">
            {{ deadline }}
          </p>
        </div>
      </div>
    </div>

    <div style="flex: 1; display: flex; flex-direction: column;">
      <div style="height: 40px; padding: 8px 16px 0 24px;">
        <p style="
            font-size: 14px;
            color: rgb(var(--mdui-color-on-surface-variant));
            margin: 0;
          ">
          {{ content }}
        </p>
      </div>
      <div style="
          flex: 1;
          display: flex;
          justify-content: flex-end;
          align-items: flex-end;
          padding: 0 16px 16px 0;
        ">
        <mdui-button class="on-surface-variant" variant="outlined" style="margin-right: 8px;"
          @click.stop="onButtonClick">
          忽略
        </mdui-button>
        <mdui-button variant="filled" @click.stop="onButtonClick">
          提交
        </mdui-button>
      </div>
    </div>
  </mdui-card>
</template>

<script setup>
const props = defineProps({
  selected: Boolean,
  title: String,
  deadline: String,
  content: String,
});

function onButtonClick() {
  console.log('按钮被点击');
}
</script>

<style scoped>
.card-default {
  border-radius: var(--mdui-shape-corner-medium);
  height: 200px;
  display: flex;
  flex-direction: column;
  padding: 0;
  box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
  background-color: rgb(var(--mdui-color-surface));
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
  height: 200px;
  display: flex;
  flex-direction: column;
  padding: 0;
  box-shadow: none;
  background-color: rgb(var(--mdui-color-on-primary));
  cursor: default;
  transition: box-shadow 0.2s ease;
}

.card-selected:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: default;
}
</style>
