import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { AdditiveBlending, BufferAttribute, Group, Points } from "three";

type Scene3DProps = {
  result: unknown;
};

function ParticleField() {
  const pointsRef = useRef<Points>(null);
  const geometry = useMemo(() => {
    const positions = new Float32Array(900);

    for (let i = 0; i < positions.length; i += 3) {
      positions[i] = (Math.random() - 0.5) * 18;
      positions[i + 1] = (Math.random() - 0.5) * 10;
      positions[i + 2] = (Math.random() - 0.5) * 12;
    }

    return positions;
  }, []);

  useFrame((_, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.035;
      pointsRef.current.rotation.x += delta * 0.012;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[geometry, 3]} />
      </bufferGeometry>
      <pointsMaterial
        blending={AdditiveBlending}
        color="#38bdf8"
        depthWrite={false}
        opacity={0.45}
        size={0.035}
        transparent
      />
    </points>
  );
}

function RainField() {
  const rainRef = useRef<Points>(null);
  const geometry = useMemo(() => {
    const positions = new Float32Array(540);

    for (let i = 0; i < positions.length; i += 3) {
      positions[i] = (Math.random() - 0.5) * 14;
      positions[i + 1] = Math.random() * 7 - 1;
      positions[i + 2] = (Math.random() - 0.5) * 7;
    }

    return positions;
  }, []);

  useFrame((_, delta) => {
    if (!rainRef.current) {
      return;
    }

    const attribute = rainRef.current.geometry.getAttribute("position") as BufferAttribute;
    for (let index = 0; index < attribute.count; index += 1) {
      const nextY = attribute.getY(index) - delta * 2.4;
      if (nextY < -4) {
        attribute.setY(index, 4);
      } else {
        attribute.setY(index, nextY);
      }
    }
    attribute.needsUpdate = true;
  });

  return (
    <points ref={rainRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[geometry, 3]} />
      </bufferGeometry>
      <pointsMaterial color="#7dd3fc" opacity={0.28} size={0.045} transparent />
    </points>
  );
}

function Globe({ active }: { active: boolean }) {
  const groupRef = useRef<Group>(null);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * (active ? 0.18 : 0.08);
      groupRef.current.rotation.z = Math.sin(Date.now() * 0.00035) * 0.08;
    }
  });

  const nodePositions = [
    [-1.8, 0.8, 0.4],
    [1.7, 0.4, -0.3],
    [0.2, -1.5, 0.8],
    [-0.7, 1.6, -0.9],
    [1.0, -0.7, 1.2],
  ];

  return (
    <group ref={groupRef} position={[1.8, 0.1, -1]}>
      <mesh>
        <sphereGeometry args={[2.15, 64, 64]} />
        <meshStandardMaterial color="#07110d" metalness={0.7} roughness={0.32} />
      </mesh>
      <mesh>
        <sphereGeometry args={[2.19, 64, 64]} />
        <meshBasicMaterial color={active ? "#22c55e" : "#38bdf8"} opacity={0.13} transparent wireframe />
      </mesh>
      <mesh rotation={[1.1, 0.2, 0.4]}>
        <torusGeometry args={[2.42, 0.012, 8, 160]} />
        <meshBasicMaterial color="#38bdf8" opacity={0.5} transparent />
      </mesh>
      <mesh rotation={[0.2, 1.4, -0.5]}>
        <torusGeometry args={[2.62, 0.01, 8, 160]} />
        <meshBasicMaterial color="#facc15" opacity={0.28} transparent />
      </mesh>
      {nodePositions.map((position, index) => (
        <group key={index} position={position as [number, number, number]}>
          <mesh>
            <sphereGeometry args={[0.075, 16, 16]} />
            <meshBasicMaterial color={index % 2 === 0 ? "#22c55e" : "#38bdf8"} />
          </mesh>
          <mesh>
            <sphereGeometry args={[0.16, 16, 16]} />
            <meshBasicMaterial color="#ffffff" opacity={0.08} transparent />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function FloatingCrops() {
  const groupRef = useRef<Group>(null);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y -= delta * 0.12;
      groupRef.current.position.y = Math.sin(Date.now() * 0.0008) * 0.08;
    }
  });

  const crops = [
    [-3.3, 1.6, -0.6],
    [-2.5, -1.1, 0.4],
    [3.8, 1.7, -1.4],
    [2.9, -1.7, 0.2],
  ];

  return (
    <group ref={groupRef}>
      {crops.map((position, index) => (
        <group key={index} position={position as [number, number, number]} rotation={[0.2, index, -0.35]}>
          <mesh>
            <coneGeometry args={[0.13, 0.62, 6]} />
            <meshStandardMaterial color="#22c55e" emissive="#082f1a" roughness={0.38} />
          </mesh>
          <mesh position={[0, -0.36, 0]}>
            <cylinderGeometry args={[0.018, 0.018, 0.46, 8]} />
            <meshStandardMaterial color="#facc15" emissive="#2b2105" />
          </mesh>
        </group>
      ))}
    </group>
  );
}

export default function Scene3D({ result }: Scene3DProps) {
  const active = Boolean(result);

  return (
    <div className="scene-backdrop" aria-hidden="true">
      <Canvas camera={{ fov: 45, position: [0, 0, 7.5] }} dpr={[1, 1.5]}>
        <color attach="background" args={["#050505"]} />
        <ambientLight intensity={0.45} />
        <pointLight color="#38bdf8" intensity={2.2} position={[2.5, 3, 3]} />
        <pointLight color="#22c55e" intensity={1.5} position={[-4, -2, 2]} />
        <Globe active={active} />
        <FloatingCrops />
        <ParticleField />
        <RainField />
      </Canvas>
    </div>
  );
}
