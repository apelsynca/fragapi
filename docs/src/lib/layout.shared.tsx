import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import { appName, gitConfig } from "./shared";
import { i18n } from "./i18n";
import { uiTranslations } from "fumadocs-ui/i18n";

export const translations = i18n
  .translations()
  .extend(uiTranslations())
  .add({
    ru: {
      displayName: "Русский",
    },
    en: {
      displayName: "English",
    },
  });

export function baseOptions(locale: string): BaseLayoutProps {
  return {
    nav: {
      // JSX supported
      title: appName,
    },
    githubUrl: `https://github.com/${gitConfig.user}/${gitConfig.repo}`,
  };
}
