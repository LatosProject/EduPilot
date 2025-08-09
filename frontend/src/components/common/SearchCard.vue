<template>
  <mdui-card clickable style="
      border-radius: var(--mdui-shape-corner-extra-large);
      height: 56px;
      display: flex;
      align-items: center;
      padding: 0;
      gap: 0;
      box-shadow: none;
      background-color: rgb(var(--mdui-color-surface-container-high));
    ">
    <mdui-icon name="search" style="
        font-size: 24px;
        color: rgb(var(--mdui-color-on-surface-variant));
        margin: 0 16px;
        user-select: none;
      "></mdui-icon>

    <div style="
        font-size: 16px;
        line-height: 24px;
        letter-spacing: 0.5px;
        font-weight: 400;
        font-family: 'Roboto';
        user-select: none;
        color: rgb(var(--mdui-color-on-surface-variant));
      ">
      搜索
    </div>

    <mdui-button-icon icon="account_circle" style="margin-left: auto; margin-right: 8px"></mdui-button-icon>
  </mdui-card>
</template>
