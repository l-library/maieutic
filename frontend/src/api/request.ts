import createClient from "openapi-fetch";
import type {paths} from "./types.ts";

const client = createClient<paths>(
    {
        baseUrl: import.meta.env.API_BASE_URL
    }
)
export {client} ;