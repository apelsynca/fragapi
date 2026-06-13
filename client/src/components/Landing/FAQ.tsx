import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '#/components/ui/accordion'
import { Section } from '#/components/ui/section'
import { m } from '#/paraglide/messages'

interface FAQItemProps {
  question: string
  answer: React.ReactNode
  value?: string
}

interface FAQProps {
  title?: string
  items?: FAQItemProps[] | false
  className?: string
}

export default function FAQ({
  title = m.faq_title(),
  items = [
    {
      question: 'Почему FragAPI?',
      answer: (
        <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
          Не нужно KYC, низкая комса 0.5% (не 50%)
        </p>
      ),
    },
  ],
  className,
}: FAQProps) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-8">
        <h2 className="text-center text-3xl font-semibold sm:text-5xl">
          {title}
        </h2>
        {items !== false && items.length > 0 && (
          <Accordion type="single" collapsible className="w-full max-w-200">
            {items.map((item, index) => (
              <AccordionItem
                key={item.value ?? item.question}
                value={item.value || `item-${index + 1}`}
              >
                <AccordionTrigger>{item.question}</AccordionTrigger>
                <AccordionContent>{item.answer}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        )}
      </div>
    </Section>
  )
}
