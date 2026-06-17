import { generateFiles } from "fumadocs-openapi";
import { openapi } from "@/lib/openapi";

void generateFiles({
  input: openapi,
  output: "./content/docs/api",
  includeDescription: true,
  meta: true,
  per: "operation",
  name(output) {
    const doc = this.document;
    if (output.type === "operation") {
      const operation = doc.paths![output.item.path]![output.item.method]!;
      return operation.operationId!.replace(/:/g, "/");
    }

    const hook = this.dereferenceShallow(doc.webhooks![output.item.name])[
      output.item.method
    ]!;
    // webhook object
    console.log(hook);
    return "my-dir/filename";
  },
});
