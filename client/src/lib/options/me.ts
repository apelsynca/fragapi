import { queryOptions } from "@tanstack/react-query";

import { fetchMe } from "../user";

export const meQueryOptions = () =>
  queryOptions({
    queryKey: ["me"],
    queryFn: () => fetchMe(),
  });
