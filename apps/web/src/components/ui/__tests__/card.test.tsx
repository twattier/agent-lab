import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '../card';

describe('Card', () => {
  it('renders card with children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('custom-class');
  });

  it('renders with all card components', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card Description</CardDescription>
        </CardHeader>
        <CardContent>Card Content</CardContent>
        <CardFooter>Card Footer</CardFooter>
      </Card>
    );

    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card Description')).toBeInTheDocument();
    expect(screen.getByText('Card Content')).toBeInTheDocument();
    expect(screen.getByText('Card Footer')).toBeInTheDocument();
  });
});

describe('CardHeader', () => {
  it('renders header with children', () => {
    render(<CardHeader>Header content</CardHeader>);
    expect(screen.getByText('Header content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <CardHeader className="custom-header">Content</CardHeader>
    );
    const header = container.firstChild as HTMLElement;
    expect(header).toHaveClass('custom-header');
  });
});

describe('CardTitle', () => {
  it('renders title as h3 element', () => {
    render(<CardTitle>Test Title</CardTitle>);
    const title = screen.getByText('Test Title');
    expect(title.tagName).toBe('H3');
  });

  it('applies custom className', () => {
    render(<CardTitle className="custom-title">Title</CardTitle>);
    const title = screen.getByText('Title');
    expect(title).toHaveClass('custom-title');
  });
});

describe('CardDescription', () => {
  it('renders description as p element', () => {
    render(<CardDescription>Test Description</CardDescription>);
    const description = screen.getByText('Test Description');
    expect(description.tagName).toBe('P');
  });

  it('applies custom className', () => {
    render(
      <CardDescription className="custom-desc">Description</CardDescription>
    );
    const description = screen.getByText('Description');
    expect(description).toHaveClass('custom-desc');
  });
});

describe('CardContent', () => {
  it('renders content with children', () => {
    render(<CardContent>Content text</CardContent>);
    expect(screen.getByText('Content text')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <CardContent className="custom-content">Content</CardContent>
    );
    const content = container.firstChild as HTMLElement;
    expect(content).toHaveClass('custom-content');
  });

  it('renders complex content', () => {
    render(
      <CardContent>
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
      </CardContent>
    );
    expect(screen.getByText('Paragraph 1')).toBeInTheDocument();
    expect(screen.getByText('Paragraph 2')).toBeInTheDocument();
  });
});

describe('CardFooter', () => {
  it('renders footer with children', () => {
    render(<CardFooter>Footer content</CardFooter>);
    expect(screen.getByText('Footer content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <CardFooter className="custom-footer">Footer</CardFooter>
    );
    const footer = container.firstChild as HTMLElement;
    expect(footer).toHaveClass('custom-footer');
  });

  it('renders with multiple children', () => {
    render(
      <CardFooter>
        <button>Cancel</button>
        <button>Submit</button>
      </CardFooter>
    );
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Submit')).toBeInTheDocument();
  });
});

describe('Card composition', () => {
  it('renders a complete card structure', () => {
    render(
      <Card data-testid="card">
        <CardHeader>
          <CardTitle>Project Dashboard</CardTitle>
          <CardDescription>View all your projects</CardDescription>
        </CardHeader>
        <CardContent>
          <p>You have 5 active projects</p>
        </CardContent>
        <CardFooter>
          <button>View All</button>
        </CardFooter>
      </Card>
    );

    expect(screen.getByText('Project Dashboard')).toBeInTheDocument();
    expect(screen.getByText('View all your projects')).toBeInTheDocument();
    expect(screen.getByText('You have 5 active projects')).toBeInTheDocument();
    expect(screen.getByText('View All')).toBeInTheDocument();
  });

  it('renders card without header', () => {
    render(
      <Card>
        <CardContent>Content only</CardContent>
      </Card>
    );
    expect(screen.getByText('Content only')).toBeInTheDocument();
  });

  it('renders card without footer', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Title</CardTitle>
        </CardHeader>
        <CardContent>Content</CardContent>
      </Card>
    );
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});
