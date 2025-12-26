import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

const features = [
  {
    title: 'ROS 2',
    description: 'Learn Robot Operating System 2 for controlling physical robots and simulations.',
    link: '/docs/ros2/intro',
  },
  {
    title: 'Digital Twin',
    description: 'Understand how to create digital replicas of real-world systems for testing and analysis.',
    link: '/docs/digital-twin/intro',
  },
  {
    title: 'AI-Robot Brain',
    description: 'Explore AI integration for humanoid robotics and autonomous decision-making.',
    link: '/docs/ai-robot-brain/intro',
  },
  {
    title: 'VLA',
    description: 'Learn Virtual Learning Agents for advanced human-robot interaction scenarios.',
    link: '/docs/vla/intro',
  },
];

function Feature({title, description, link}) {
  return (
    <div className={clsx('col col--6', styles.feature)}>
      <div className="card">
        <div className="card__body">
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
        <div className="card__footer">
          <Link className="button button--primary" to={link}>Explore Module</Link>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="Bridging the gap between the digital brain and the physical body">
      <header className={clsx('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title">Physical AI & Humanoid Robotics</h1>
          <p className="hero__subtitle">Bridging the gap between the digital brain and the physical body</p>
        </div>
      </header>
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
