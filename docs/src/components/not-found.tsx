import { i18n } from "@/lib/i18n";
import { baseOptions } from "@/lib/layout.shared";
import { HomeLayout } from "fumadocs-ui/layouts/home";
import { DefaultNotFound } from "fumadocs-ui/layouts/home/not-found";

export function NotFound() {
  // TODO: if 'ru' / 'en' present in pathname, use them, otherwise default language
  return (
    <HomeLayout {...baseOptions(i18n.defaultLanguage)}>
      <DefaultNotFound />
    </HomeLayout>
  );
}
