import { GithubInfo } from "./github-info";

export const Repositories = () => {
  return (
    <div className="flex flex-col md:flex-row p-4 bg-black rounded-xl">
      <GithubInfo
        className="bg-gray-800 px-4"
        owner="apelsynca"
        repo="fragapi"
      />
    </div>
  );
};
