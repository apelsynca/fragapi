import * as React from 'react'
import { format } from 'date-fns'
import { Calendar as CalendarIcon } from 'lucide-react'

import { Button } from '#/components/ui/button'
import { Calendar } from '#/components/ui/calendar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '#/components/ui/popover'
import { cn } from '#/lib/utils'

export function DatePicker({
  date,
  setDate,
}: {
  date?: Date
  setDate: React.Dispatch<React.SetStateAction<Date | undefined>>
}) {
  const [open, setOpen] = React.useState<boolean>(false)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          data-empty={!date}
          className={cn(
            'w-70 justify-start text-left font-normal',
            date ? 'text-green-200' : 'text-yellow-200',
          )}
        >
          <CalendarIcon />
          {date ? format(date, 'PPP') : <span>Вечный</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar mode="single" selected={date} onSelect={setDate} />
        <div className="p-1">
          <Button
            className="w-full"
            onClick={() => {
              setDate(undefined)
              setOpen(false)
            }}
          >
            Вечный
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  )
}
