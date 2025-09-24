import { Skeleton } from "../ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

const LoadingRow = () => (
  <TableRow>
    <TableCell>
      <Skeleton className="h-3 max-w-[5rem]" />
    </TableCell>
    <TableCell>
      <Skeleton className="h-3 max-w-[5rem]" />
    </TableCell>
    <TableCell>
      <Skeleton className="h-3 max-w-[12rem]" />
    </TableCell>
  </TableRow>
);

export const TransactionsLoading = () => {
  return (
    <Table className="mt-6">
      <TableHeader>
        <TableHead>
          <Skeleton className="h-2 max-w-[3rem]" />
        </TableHead>
        <TableHead>
          <Skeleton className="h-2 max-w-[5rem]" />
        </TableHead>
        <TableHead>
          <Skeleton className="h-2 max-w-[3rem]" />
        </TableHead>
      </TableHeader>
      <TableBody>
        <LoadingRow />
        <LoadingRow />
        <LoadingRow />
      </TableBody>
    </Table>
  );
};
