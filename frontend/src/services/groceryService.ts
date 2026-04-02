const baseURL = "http://localhost:8000";
import axios from "axios"

export type GroceryRequest = {
    prompt: string
}

export type GroceryResponse = {
  prompt: string;
  answer: string;
}

export async function getGroceryRecs(
    prompt: GroceryRequest
): Promise<GroceryResponse> {
    const res = await axios.post(`${baseURL}/api/grocery-recs`, prompt)
    return res.data
}