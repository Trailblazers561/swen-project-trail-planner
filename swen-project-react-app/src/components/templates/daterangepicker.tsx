import { format } from "date-fns"
import { CalendarIcon } from "lucide-react"
import { type DateRange } from "react-day-picker"
import { Button } from "@/components/templates/button"
import { Calendar } from "@/components/templates/calendar"
import { Field } from "@/components/templates/field"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/templates/popover"
import { subMonths } from "date-fns";

type DatePickerWithRangeProps = {
  value?: DateRange
  onChange: (range: DateRange | undefined) => void
}


export function DatePickerWithRange({ value, onChange }: DatePickerWithRangeProps) {
  const date: DateRange | undefined = value;

  const handleSelect = ( rangeItGivesMeIDontWantIt: DateRange | undefined, selectedDay: Date) => {
    if (!selectedDay) return;

    // If there is a completed date range then reset
    if (date?.from && date?.to) {
      onChange({from: selectedDay, to: undefined});
    } else {
      const newRange: DateRange = {from: undefined, to: undefined}

      if (date?.from) 
        newRange.from = date.from;
      if (date?.to)
        newRange.from = date.to;
      newRange.to = selectedDay;

      if (newRange.from && newRange.to < newRange.from) {
        const swap = newRange.from;
        newRange.from = newRange.to;
        newRange.to = swap;
      }

      onChange(newRange);
    }
  }

  return (
    <Field className="mx-auto w-60">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            id="date-picker-range"
            className="justify-start px-2.5 font-normal"
          >
            <CalendarIcon />
            {date?.from ? (
              date.to ? (
                <>
                  {format(date.from, "LLL dd, y")} -{" "}
                  {format(date.to, "LLL dd, y")}
                </>
              ) : (
                format(date.from, "LLL dd, y")
              )
            ) : (
              <span>Pick a date</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0 z-10000" align="start" data-testid="calandar-popup">
          <Calendar
            mode="range"
            defaultMonth={subMonths((date?.to ?? date?.from ?? new Date()) , 1)}
            selected={date}
            onSelect={handleSelect}
            numberOfMonths={2}
            captionLayout="dropdown"
          />
        </PopoverContent>
      </Popover>
    </Field>
  )
}
