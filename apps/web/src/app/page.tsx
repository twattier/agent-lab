import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">AgentLab</h1>
      <p className="mt-4 text-lg text-gray-600">
        AI Project Management Platform
      </p>
      <div className="mt-8 flex gap-4">
        <Button>Get Started</Button>
        <Button variant="outline">Learn More</Button>
      </div>
    </main>
  )
}
