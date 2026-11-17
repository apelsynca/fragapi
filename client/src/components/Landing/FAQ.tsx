import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '#/components/ui/accordion'
import { Section } from '#/components/ui/section'
import { siteConfig } from '#/config'
import { m } from '#/paraglide/messages'

export default function FAQ() {
  const items = [
    { question: m.faq_q1(), answer: m.faq_a1() },
    { question: m.faq_q2(), answer: m.faq_a2() },
    { question: m.faq_q3(), answer: m.faq_a3() },
    { question: m.faq_q4(), answer: m.faq_a4() },
    { question: m.faq_q5(), answer: m.faq_a5() },
  ]

  return (
    <Section className="w-full py-20">
      <div className="max-w-container mx-auto flex flex-col items-center gap-8">
        <h2 className="text-center text-3xl font-semibold tracking-[-0.02em] sm:text-5xl sm:leading-14">
          {m.faq_title()}
        </h2>
        <div className="flex w-full max-w-190 flex-col gap-6">
          <Accordion type="single" collapsible>
            {items.map((item, index) => (
              <AccordionItem key={item.question} value={`item-${index + 1}`}>
                <AccordionTrigger className="items-center py-4.5 text-base">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent>
                  <p className="text-muted-foreground max-w-160 pb-2 text-[15px] leading-6">
                    {item.answer}
                  </p>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
          <p className="text-muted-foreground text-center text-sm">
            {m.faq_note()}{' '}
            <a
              className="text-foreground font-medium"
              href={siteConfig.telegramChat}
            >
              {m.faq_note_link()}
            </a>
          </p>
        </div>
      </div>
    </Section>
  )
}
