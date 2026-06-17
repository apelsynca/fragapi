import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import { uiTranslations } from "fumadocs-ui/i18n";
import { openapiTranslations } from "fumadocs-openapi/i18n";
import { appName, gitConfig } from "./shared";
import { i18n } from "./i18n";

export const translations = i18n
  .translations()
  .extend(uiTranslations())
  .extend(openapiTranslations())
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
      url: `/${locale}`,
    },
    githubUrl: `https://github.com/${gitConfig.user}/${gitConfig.repo}`,
    links: [
      {
        type: "button",
        text: locale === "ru" ? "В панель" : "To dashboard",
        url: "https://fragapi.com",
        secondary: true,
      },
    ],
  };
}
