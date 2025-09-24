import { queryOptions } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";

import { fetchMe } from "../user";

export const meQueryOptions = () =>
  queryOptions({
    queryKey: ["me"],
    queryFn: useServerFn(fetchMe),
  });
