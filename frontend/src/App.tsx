import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm, useWatch } from "react-hook-form"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldGroup,
  FieldLabel,
  FieldError,
  FieldDescription,
} from "@/components/ui/field";
import {
  InputGroup,
  InputGroupTextarea,
  InputGroupAddon,
  InputGroupText,
} from "@/components/ui/input-group";
import * as z from "zod"
import { getGroceryRecs } from "@/services/groceryService"
import { useState } from 'react'

const formSchema = z.object({
  prompt: z.string().min(5, "Prompt must be at least 5 characters").max(250, "Prompt cannot exceed 250 characters")
})

type GroceryItem = {
  name: string
  brand: string
  store: string
  category: string
  price: string
  snap: boolean
}

function parseResponseLine(line: string): GroceryItem | null {
  try {
    const nameMatch = line.match(/^(.+?) by (.+?) at (.+?)\. Category: (.+?)\. Price: (.+?)\. (SNAP eligible|not SNAP eligible)/)
    if (!nameMatch) return null
    return {
      name: nameMatch[1].trim(),
      brand: nameMatch[2].trim(),
      store: nameMatch[3].trim(),
      category: nameMatch[4].trim(),
      price: nameMatch[5].trim(),
      snap: nameMatch[6] === "SNAP eligible"
    }
  } catch {
    return null
  }
}

function GroceryCard({ item }: { item: GroceryItem }) {
  const isOnSale = item.price.includes("on sale")
  return (
    <div className="p-4 rounded-lg border bg-card shadow-sm flex flex-col gap-1">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-semibold text-base">{item.name}</p>
          <p className="text-sm text-muted-foreground">{item.brand} · {item.store}</p>
        </div>
        <div className="text-right">
          <p className={`font-bold text-lg ${isOnSale ? "text-green-600" : ""}`}>
            {item.price.replace("regular price ", "").replace("on sale for ", "")}
          </p>
          {isOnSale && <p className="text-xs text-green-600">On Sale</p>}
        </div>
      </div>
      <div className="flex gap-2 mt-1">
        <span className="text-xs px-2 py-0.5 rounded-full bg-muted">{item.category}</span>
        {item.snap && <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">SNAP Eligible</span>}
      </div>
    </div>
  )
}

function App() {
  const {control, handleSubmit, reset, formState} = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema), 
    defaultValues: { prompt: "" }
  })
  const promptValue = useWatch({ control, name: "prompt" }) ?? ""
  const [items, setItems] = useState<GroceryItem[]>([])
  const [loading, setLoading] = useState(false)

  async function onSubmit(data: z.infer<typeof formSchema>) {
    setLoading(true)
    const rec = await getGroceryRecs(data)
    const parsed = rec.answer
      .split("\n")
      .map(parseResponseLine)
      .filter((item): item is GroceryItem => item !== null)
    setItems(parsed)
    setLoading(false)
    reset()
  }

  return (
    <Card className="w-full h-dvh">
      <CardHeader>
        <CardTitle>Grocery Finder</CardTitle>
        <CardDescription>
          Find grocery options in Charlottesville that best suit your needs.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form id="grocery-finder-form" onSubmit={handleSubmit(onSubmit)}>
          <FieldGroup>
            <Controller
              name="prompt"
              control={control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="grocery-finder-prompt">
                    Your Grocery Prompt
                  </FieldLabel>
                  <InputGroup>
                    <InputGroupTextarea
                      {...field}
                      id="grocery-finder-prompt"
                      placeholder="e.g. I need organic eggs and almond milk near UVA, budget around $20"
                      rows={4}
                      className="min-h-24 resize-none"
                      aria-invalid={fieldState.invalid}
                    />
                    <InputGroupAddon align="block-end">
                      <InputGroupText className="tabular-nums">
                        {field.value.length}/250 characters
                      </InputGroupText>
                    </InputGroupAddon>
                  </InputGroup>
                  <FieldDescription>
                    Include your location, budget, and the items you need.
                  </FieldDescription>
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
          </FieldGroup>
        </form>
      </CardContent>
      <CardFooter>
        <Field orientation="horizontal">
          <Button type="button" variant="outline" onClick={() => reset()} disabled={!promptValue.length}>
            Reset
          </Button>
          <Button type="submit" form="grocery-finder-form" disabled={!formState.isValid || loading}>
            {loading ? "Searching..." : "Find Groceries"}
          </Button>
        </Field>
      </CardFooter>
      <CardContent>
        {items.length > 0 && (
          <div className="flex flex-col gap-3 mt-2">
            {items.map((item, index) => (
              <GroceryCard key={index} item={item} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default App