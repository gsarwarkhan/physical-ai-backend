import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import styles from './index.module.css';

const features = [
  {
    title: 'ROS 2',
    description: 'Learn Robot Operating System 2 for controlling physical robots and simulations.',
    link: '/docs/01-Module-1-ROS2/intro',
  },
  {
    title: 'Digital Twin',
    description: 'Understand how to create digital replicas of real-world systems for testing and analysis.',
    link: '/docs/02-Module-2-Digital-Twin/intro',
  },
  {
    title: 'AI-Robot Brain',
    description: 'Explore AI integration for humanoid robotics and autonomous decision-making.',
    link: '/docs/03-Module-3-Isaac-Sim/intro',
  },
  {
    title: 'VLA',
    description: 'Learn Virtual Learning Agents for advanced human-robot interaction scenarios.',
    link: '/docs/04-Module-4-VLA/intro',
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
          <a className="button button--primary" href={link}>Explore Module</a>
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
