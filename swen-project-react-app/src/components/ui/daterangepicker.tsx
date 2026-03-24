"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Field, FieldLabel } from "@/components/ui/field"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { addDays, format, set } from "date-fns"
import { CalendarIcon } from "lucide-react"
import { type DateRange } from "react-day-picker"

interface DateRangePickerProps {
    value?: DateRange
    onChange?: (range: DateRange | undefined) => void
}

export function DateRangePicker({ value, onChange }: DateRangePickerProps) {
const [internalDate, setInternalDate] = React.useState<DateRange | undefined>(
    value
)

const date = value ?? internalDate

function handleSelect(range: DateRange | undefined) {
    if(!value) {
        setInternalDate(range)
    }
    onChange?.(range)
  }

  return (
    <Field className="mx-auto w-60">
      <Popover>
        <PopoverTrigger asChild>
          <Button variant="primary" id="date-picker-range" className="justify-start px-2.5 font-normal bg-white text-black border border-black hover:bg-gray-100">
            <CalendarIcon />
            {date?.from && date?.to
            ? `${format(date.from, "LLL dd y")} - ${format(date.to, "LLL dd y")}`
            : "Pick a date"}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0 bg-white text-black border border-gray-300 shadow-md" align="start" data-testid="calandar-popup">
          <Calendar
            mode="range"
            selected={date}
            onSelect={handleSelect}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
    </Field>
  )
}