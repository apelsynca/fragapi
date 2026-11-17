import {
  ChartColumnIcon,
  CrownIcon,
  GiftIcon,
  SendIcon,
  StarIcon,
  WalletIcon,
} from 'lucide-react'
import SectionHeading from './SectionHeading'
import { m } from '#/paraglide/messages'

export default function Features() {
  const features = [
    {
      icon: StarIcon,
      title: m.land_feature_stars_title(),
      text: m.land_feature_stars_text(),
      chip: 'POST /v1/stars/buy',
    },
    {
      icon: CrownIcon,
      title: m.land_feature_premium_title(),
      text: m.land_feature_premium_text(),
      chip: 'POST /v1/premium/buy',
    },
    {
      icon: GiftIcon,
      title: m.land_feature_gifts_title(),
      text: m.land_feature_gifts_text(),
      chip: 'GET /v1/gifts/{short_name}/models',
    },
    {
      icon: WalletIcon,
      title: m.land_feature_deposit_title(),
      text: m.land_feature_deposit_text(),
      chip: 'POST /v1/deposits/ton',
    },
    {
      icon: SendIcon,
      title: m.land_feature_logs_title(),
      text: m.land_feature_logs_text(),
      chip: m.land_feature_logs_chip(),
    },
    {
      icon: ChartColumnIcon,
      title: m.land_feature_stats_title(),
      text: m.land_feature_stats_text(),
      chip: 'GET /v1/transactions',
    },
  ]

  return (
    <section className="w-full px-4 pt-20 sm:pt-32">
      <div className="mx-auto flex max-w-280 flex-col gap-14">
        <SectionHeading
          eyebrow={m.land_features_eyebrow()}
          title={m.land_features_title()}
          subtitle={m.land_features_subtitle()}
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, text, chip }) => (
            <div
              key={title}
              className="border-border flex flex-col items-start gap-5 rounded-2xl border bg-white/3 p-7"
            >
              <div className="bg-brand/12 text-brand flex size-11 items-center justify-center rounded-xl">
                <Icon className="size-5" />
              </div>
              <div className="flex flex-col gap-2">
                <h3 className="text-xl leading-7 font-semibold">{title}</h3>
                <p className="text-muted-foreground text-[15px] leading-6">
                  {text}
                </p>
              </div>
              <code className="text-muted-foreground rounded-md bg-white/5 px-2 py-1 font-mono text-xs leading-4">
                {chip}
              </code>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
