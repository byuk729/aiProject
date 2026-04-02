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
  prompt: z.string().min(20, "Prompt must be at least 20 characters").max(250, "Prompt cannot exceed 500 characters")
})

function App() {
  const {control, handleSubmit, reset, formState} = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema), 
    defaultValues: {
      prompt: ""
    }
  })
  const promptValue = useWatch({ control, name: "prompt" }) ?? ""

  const [response, setResponse] = useState("")
  async function onSubmit(data: z.infer<typeof formSchema>) {
    const rec = await getGroceryRecs(data)
    setResponse(rec.answer)
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
          <Button type="submit" form="grocery-finder-form" disabled={!formState.isValid}>
            Find Groceries
          </Button>
        </Field>
      </CardFooter>
      <CardContent>
            {response}
      </CardContent>
    </Card>
  )
}

export default App
