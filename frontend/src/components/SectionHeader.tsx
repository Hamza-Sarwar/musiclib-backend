import Link from 'next/link';

interface SectionHeaderProps {
  title: string;
  href?: string;
}

export default function SectionHeader({ title, href }: SectionHeaderProps) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h2 className="text-lg font-semibold text-white">{title}</h2>
      {href && (
        <Link
          href={href}
          className="text-sm text-primary-400 transition hover:text-primary-300"
        >
          See all &rarr;
        </Link>
      )}
    </div>
  );
}
