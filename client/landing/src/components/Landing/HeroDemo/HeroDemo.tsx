import DemoApiPanel from './DemoApiPanel'
import DemoChart from './DemoChart'
import { DemoSidebar, DemoTopBar } from './DemoShell'
import DemoStats from './DemoStats'
import DemoTransactions from './DemoTransactions'
import { useDemoLoop } from './useDemoLoop'

/**
 * The dashboard, rebuilt as live markup on scripted data: API requests go out
 * and the balance, chart and transactions react to them.
 */
export default function HeroDemo() {
  const { ref, state, send } = useDemoLoop<HTMLDivElement>()

  return (
    <div
      ref={ref}
      role="group"
      aria-label="Живое демо панели FragAPI: отправьте пробный запрос к API"
      className="bg-sidebar flex h-160 w-full overflow-hidden text-left text-sm select-none"
    >
      <DemoSidebar />
      <div className="flex min-w-0 flex-1 md:p-2 md:pl-0">
        <div className="bg-background flex min-w-0 flex-1 flex-col md:rounded-xl">
          <DemoTopBar />
          <div className="flex min-h-0 gap-2.5 p-3 sm:p-4">
            <div className="flex min-w-0 flex-1 flex-col gap-2.5">
              <DemoStats state={state} />
              <DemoChart chart={state.chart} />
              <DemoTransactions rows={state.rows} />
            </div>
            <DemoApiPanel state={state} onSend={send} />
          </div>
        </div>
      </div>
    </div>
  )
}
