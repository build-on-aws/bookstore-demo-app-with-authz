import fs from "fs/promises";

import { SSMClient, GetParametersByPathCommand } from "@aws-sdk/client-ssm";

try {
  const args = process.argv.slice(2);
  const environmentType = args[0] ? args[0] : "";
  const client = new SSMClient();

  const region = await client.config.region();

  const query = {
    Path: "/bookstore-demo-app-with-authz/",
    WithDecryption: false,
    Recursive: true,
  };

  const requiredParams = ["PRODUCT_SERVICE_API_URL", "USER_POOL_ID", "USER_POOL_CLIENT_ID"];

  const command = new GetParametersByPathCommand(query);
  const params = await client.send(command);
  const output = [];

  const formatParams = (data) => {
    for (const param of data) {
      const paramName = param.Name.toUpperCase().split("/").pop().replace(/-/g, "_");

      if (requiredParams.includes(paramName)) {
        output.push(`VUE_APP_${paramName}=${param.Value}`);
      }
    }
  };

  let fileName = "./.env";

  if (environmentType) {
    fileName += `.${environmentType}`;
  }

  formatParams(params.Parameters);
  output.push(`VUE_APP_AWS_REGION=${region}`);

  await fs.writeFile(fileName, output.join("\n"));

  console.log(`Environment file ${fileName} populated with configuration parameters.`);
} catch (error) {
  console.log(`Error: ${error}`);
}
