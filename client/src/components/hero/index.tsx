import { ExternalLink } from "lucide-react";

import { Button } from "~/components/ui/button";
import { HeroLogin } from "./login";
import Beams from "../layout/beams";

export const AppHero: React.FC<{ isLoggedIn: boolean }> = ({ isLoggedIn }) => (
  <section className="relative overflow-hidden py-32 flex w-full h-screen items-center">
    <div className="absolute h-full w-full min-w-screen min-h-screen">
      <Beams
        beamWidth={2}
        beamHeight={12}
        beamNumber={12}
        lightColor="#ffcc66"
        speed={2.5}
        noiseIntensity={1.75}
        scale={0.25}
        rotation={15}
      />
    </div>
    <div className="relative z-10 container w-full mx-auto">
      <div className="mx-auto flex max-w-5xl flex-col items-center">
        <div className="flex flex-col items-center gap-6 text-center">
          <div>
            <h1 className="mb-6 text-2xl font-bold tracking-tight text-pretty lg:text-5xl">
              Используйте удобное Fragment API
            </h1>
            <p className="mx-auto max-w-3xl text-muted-foreground lg:text-xl">
              Весь функционал fragment, без KYC, без 24-х слов, в виде API.
            </p>
          </div>
          <div className="mt-6 flex justify-center gap-3">
            <HeroLogin isLoggedIn={isLoggedIn} />
            <a href="https://docs.fragapi.ru">
              <Button variant="outline" className="group">
                Узнать больше{" "}
                <ExternalLink className="ml-2 h-4 transition-transform group-hover:translate-x-0.5" />
              </Button>
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>
);
