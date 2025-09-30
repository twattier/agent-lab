import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Project } from '@/types/api'

interface ProjectCardProps {
  project: Project
  onSelect?: (id: string) => void
}

export function ProjectCard({ project, onSelect }: ProjectCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{project.name}</CardTitle>
        <CardDescription>{project.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium">Status: {project.status}</p>
            <p className="text-sm text-muted-foreground">Type: {project.projectType}</p>
          </div>
          {onSelect && (
            <Button onClick={() => onSelect(project.id)} size="sm">
              View Details
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
