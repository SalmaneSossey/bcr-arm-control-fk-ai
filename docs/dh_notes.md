# DH Notes

## Convention Used Here

The forward kinematics scripts use an educational standard-DH style chain that matches the robot's alternating axis structure and the dimensions exposed in the existing Xacro files.

The standard DH transform used in code is:

```text
A_i = RotZ(theta_i) * TransZ(d_i) * TransX(a_i) * RotX(alpha_i)
```

## BCR Geometry Values

- `L1 = 0.200`
- `L2_offset = 0.065`
- `L3 = 0.410`
- `L4_offset = -0.065`
- `L5 = 0.310`
- `L6_offset = 0.060`
- `L7 = 0.105`

## DH Table Used In Scripts

| i | theta | d | a | alpha |
|---|---|---:|---:|---:|
| 1 | `q1` | `L1` | `0.0` | `+pi/2` |
| 2 | `q2` | `0.0` | `L2_offset` | `-pi/2` |
| 3 | `q3` | `L3` | `0.0` | `+pi/2` |
| 4 | `q4` | `0.0` | `L4_offset` | `-pi/2` |
| 5 | `q5` | `L5` | `0.0` | `+pi/2` |
| 6 | `q6` | `0.0` | `L6_offset` | `-pi/2` |
| 7 | `q7` | `L7` | `0.0` | `0.0` |

## Interpretation Note

This is a consistent DH-style approximation aligned to the URDF mechanical dimensions and alternating joint-axis pattern. For the report, state this assumption explicitly and keep the same table in both the derivation and the code discussion.
