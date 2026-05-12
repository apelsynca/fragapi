import type { ListResource } from '~/server/models/misc'

export const resourceGetNextPageParam = (
  lastPage: ListResource<any>,
  _: any,
  lastPageParam: number,
) => {
  if (
    lastPage.pagination.maxPage === lastPageParam ||
    lastPage.items.length === 0
  ) {
    return null
  }
  return lastPageParam + 1
}
